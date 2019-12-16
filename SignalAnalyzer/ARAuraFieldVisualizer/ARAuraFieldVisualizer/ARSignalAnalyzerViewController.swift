//
//  ARSignalAnalyzerViewController.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 10/21/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit
import SceneKit
import ARKit
import CoreLocation

let impact = UIImpactFeedbackGenerator()

class ARSignalAnalyzerViewController: UIViewController, ARSCNViewDelegate, MultiMagnetometerMagnitudeDelegate {
    
    @IBOutlet var arSceneView: ARSCNView!
    @IBOutlet weak var cornerLabel: UILabel!
    @IBOutlet weak var directionalToggleButton: UIButton!
    @IBOutlet weak var radialToggleButton: UIButton!
    @IBOutlet weak var toggleSpheresButton: UIButton!
    @IBOutlet weak var resetButton: UIButton!
    @IBOutlet weak var particleTypeButton: UIButton!
    
    
    var auraVoxelFieldNode: AuraVoxelFieldNode?
    var readings:[CLLocation:Double] = [:]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Load the "Box" scene from the "Experience" Reality File
        //let boxAnchor = try! Experience.loadBox()
        
        // Add the box anchor to the scene
        //arView.scene.anchors.append(boxAnchor)
        resetWorldTracking()
        
        auraVoxelFieldNode = AuraVoxelFieldNode(divisions: 5, height: 3)
        arSceneView.scene.rootNode.addChildNode(auraVoxelFieldNode!)
        
        
        arSceneView.delegate = self
        arSceneView.showsStatistics = true
        arSceneView.autoenablesDefaultLighting = true
        //arSceneView.debugOptions  = [.showConstraints, .showLightExtents, ARSCNDebugOptions.showFeaturePoints, ARSCNDebugOptions.showWorldOrigin]
        //arSceneView.showsStatistics = true
        arSceneView.automaticallyUpdatesLighting = true
        arSceneView.scene.physicsWorld.gravity = SCNVector3(0,0,0)
        
        MultiMagnetometer.shared.magnitudeDelegate = self
    }
    
    /// - Tag: ARFaceTrackingSetup
    func resetWorldTracking() {
        
        // Setup Config
        guard ARWorldTrackingConfiguration.isSupported else { return }
        let configuration = ARWorldTrackingConfiguration()
        
        // Better Shading
        configuration.isLightEstimationEnabled = true
        configuration.planeDetection = .horizontal
        
        // Better Segmentation
        if #available(iOS 13.0, *) {
            var semantics = ARConfiguration.FrameSemantics()
            semantics.insert(.bodyDetection)
            semantics.insert(.personSegmentationWithDepth)
            if ARConfiguration.supportsFrameSemantics(semantics) {
                configuration.frameSemantics = semantics
            } else {
                print("Cannot update Frame Semantics: The device doesn't support .personSegmentationWithDepth")
            }
        } else {
            print("AR Frame Semantics unavailable: iOS 13 and above is required")
        }
        
        // Initiate AR Visualization
        arSceneView.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
    }
    
    // Inserting 3D Geometry for ARHitTestResult
    func insertGeometry(for result: ARHitTestResult) {
        let boxGeometry = SCNBox(width: 0.1, height: 0.1, length: 0.1, chamferRadius: 0)
        let cube = SCNNode(geometry: boxGeometry)
         
        // Method 2: Add SCNNode at position
        let position = SCNVector3(
            result.worldTransform.columns.3.x,
            result.worldTransform.columns.3.y,
            result.worldTransform.columns.3.z)
        cube.position = position
        
        arSceneView.scene.rootNode.addChildNode(cube)
    }

    // Intercept a touch on screen and hit-test against a plane surface
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let point = touch.location(in: arSceneView)

        let result = arSceneView.hitTest(point, types: .existingPlaneUsingExtent)
        guard result.count > 0 else {
            print("No plane surfaces found")
            return
        }
        
        
        //insertGeometry(for: result.first!)
    }

    func updateMagnetometer(magnitude: Double, location: CLLocation) {
//        if readings[location] != nil {
//            readings[location] = ((readings[location]!*9) + magnitude)/10
//        } else {
//            readings[location] = magnitude
//        }
        guard let position = arSceneView.defaultCameraController.pointOfView?.position else {
            return
        }
        DispatchQueue.main.async {
            let text = magnitude.format(f: "0.00")
            self.cornerLabel.text = "\(text) µT"
            self.auraVoxelFieldNode?.updateNodes(connection: CGFloat(magnitude), microTesla: 0, position: position)
        }
    }
    
    @IBAction func radialToggleButtonTap(_ sender: Any) {
        if auraVoxelFieldNode?.isUsingRadialGravity == true {
            auraVoxelFieldNode?.isUsingRadialGravity = false
            radialToggleButton.setTitleColor(UIColor.gray, for: .normal)
        } else {
            auraVoxelFieldNode?.isUsingRadialGravity = true
            radialToggleButton.setTitleColor(UIColor.systemBlue, for: .normal)
        }
    }
    
    @IBAction func directionalToggleButtonTap(_ sender: Any) {
        if auraVoxelFieldNode?.isUsingDirectionalGravity == true {
            auraVoxelFieldNode?.isUsingDirectionalGravity = false
            directionalToggleButton.setTitleColor(UIColor.gray, for: .normal)
        } else {
            auraVoxelFieldNode?.isUsingDirectionalGravity = true
            directionalToggleButton.setTitleColor(UIColor.systemBlue, for: .normal)
        }
    }
    @IBAction func settingsButtonTap(_ sender: Any) {
    }
    
    @IBAction func toggleSphereButtonTap(_ sender: Any) {
        switch auraVoxelFieldNode!.gameMode {
        case .blue:
            auraVoxelFieldNode!.gameMode = .bright
            toggleSpheresButton.setTitleColor(.white, for: .normal)
        case .bright:
            auraVoxelFieldNode!.gameMode = .hidden
            toggleSpheresButton.setTitleColor(UIColor.gray.withAlphaComponent(0.5), for: .normal)
        case .hidden:
            auraVoxelFieldNode!.gameMode = .blue
            toggleSpheresButton.setTitleColor(.systemBlue, for: .normal)
        }
    }
    
    @IBAction func resetButtonTap(_ sender: Any) {

        arSceneView.session.pause()
        arSceneView.scene.rootNode.enumerateChildNodes { (node, stop) in
            node.removeFromParentNode()
        }
        resetWorldTracking()
        
//        guard let position = arSceneView.defaultCameraController.pointOfView?.position,
//            let rotation = arSceneView.defaultCameraController.pointOfView?.rotation else {
//            return
//        }
//        auraVoxelFieldNode?.position = position
        
        arSceneView.scene.rootNode.addChildNode(auraVoxelFieldNode!)
        auraVoxelFieldNode?.reset()

        radialToggleButton.setTitleColor(UIColor.gray, for: .normal)
        directionalToggleButton.setTitleColor(UIColor.systemBlue, for: .normal)
        toggleSpheresButton.setTitleColor(.systemBlue, for: .normal)
        particleTypeButton.setTitle("◼︎", for: .normal)
    }
    
    @IBAction func particleTypeButtonTap(_ sender: Any) {
        guard let type = auraVoxelFieldNode?.particleImageType else {
            return
        }
        switch type {
            case .square:
                auraVoxelFieldNode?.particleImageType = .hexagon
                particleTypeButton.setTitle("⎔", for: .normal)
            case .hexagon:
                auraVoxelFieldNode?.particleImageType = .fuzz
                particleTypeButton.setTitle("◎", for: .normal)
            case .fuzz:
                auraVoxelFieldNode?.particleImageType = .spark
                particleTypeButton.setTitle("✧", for: .normal)
            case .spark:
                auraVoxelFieldNode?.particleImageType = .denseSpark
                particleTypeButton.setTitle("✦", for: .normal)
            case .denseSpark:
                auraVoxelFieldNode?.particleImageType = .smoke
                particleTypeButton.setTitle("✺", for: .normal)
            case .smoke:
                auraVoxelFieldNode?.particleImageType = .mix
                particleTypeButton.setTitle("☯︎", for: .normal)
            case .mix:
                auraVoxelFieldNode?.particleImageType = .square
                particleTypeButton.setTitle("◼︎", for: .normal)
        }
    }
}
