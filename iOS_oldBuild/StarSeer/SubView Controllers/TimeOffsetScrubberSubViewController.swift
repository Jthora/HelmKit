//
//  TimeOffsetScrubberSubViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 6/5/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit

class TimeOffsetScrubberSubViewController: SubViewController, UIGestureRecognizerDelegate {
    
    var panGestureRecognizer:UIPanGestureRecognizer
    var timeOffsetLabel:UILabel
    
    enum TimeScale {
        case seconds
        case minutes
        case hours
        case days
    }
    
    var timeScale:TimeScale = .seconds {
        didSet {
            updateText()
        }
    }
    
    var timeOffset:TimeInterval = 1 {
        didSet {
            updateText()
        }
    }
    
    func updateText() {
        DispatchQueue.main.async {
            let positiveSign = self.timeOffset > 0 ? "+" : ""
            switch self.timeScale {
            case .seconds: self.timeOffsetLabel.text = "Secs: \(positiveSign)\(Int(self.timeOffset))"
            case .minutes: self.timeOffsetLabel.text = "Mins: \(positiveSign)\(Int(self.timeOffset/60))"
            case .hours: self.timeOffsetLabel.text = "Hrs: \(positiveSign)\(Int(self.timeOffset/3600))"
            case .days: self.timeOffsetLabel.text = "Days: \(positiveSign)\(Int(self.timeOffset/86400))"
            }
        }
    }
    
    init(wideNarrowContainerView:UIView, timeOffsetLabel:UILabel, panGestureRecognizer:UIPanGestureRecognizer) {
        self.panGestureRecognizer = panGestureRecognizer
        self.timeOffsetLabel = timeOffsetLabel
        super.init(view: wideNarrowContainerView)
        self.panGestureRecognizer.delegate = self
        updateText()
    }
    
    func timeOffsetGestureRecognizer(_ sender: UIPanGestureRecognizer) {
        let delta = TimeInterval(sender.velocity(in: self.view).x * CGFloat(TimeSpeedScrubberSubViewController.`$`?.warp ?? 1))
        timeOffset += delta
    }
    
    func toggleScale() {
        switch timeScale {
        case .seconds: timeScale = .minutes
        case .minutes: timeScale = .hours
        case .hours: timeScale = .days
        case .days: timeScale = .seconds
        }
    }
}
