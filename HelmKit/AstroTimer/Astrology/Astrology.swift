//
//  Astrology.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/24/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation
import SwiftAA

class Astrology {
    
    enum AspectRelation:Degree, CaseIterable {
        case conjunction = 0
        case semisextile = 30
        case novile = 40
        case semisquare = 45
        case sextile = 60
        case quintile = 72
        case square = 90
        case trine = 120
        case biquintile = 144
        case quincunx = 150
        case opposition = 180
        
        func withinRange(orbitDegreeOffset:Degree) -> Bool {
            return orbitDegreeOffset > self.rawValue - self.orb && orbitDegreeOffset < self.rawValue + self.orb
        }
        
        var orb:Degree {
            switch self {
            case .conjunction: return 8
            case .semisextile: return 2
            case .novile: return 2
            case .semisquare: return 2
            case .sextile: return 4
            case .quintile: return 2
            case .square: return 8
            case .trine: return 8
            case .biquintile: return 2
            case .quincunx: return 4
            case .opposition: return 8
            }
        }
        
        var symbol:String {
            switch self {
            case .conjunction: return "☌" // 0º ~(1...8º) orb
            case .semisextile: return "⦟" // 30º ~(1...2º) orb
            case .novile: return "⦥" // 40º ~(1...2º) orb
            case .semisquare: return "✳︎" // 45º ~(1...2º) orb  aka: octile
            case .sextile: return "✱" // 60º ~(1...2º) orb
            case .quintile: return "⌿" // 72º ~(1...2º) orb
            case .square: return "⦜" // 90º ~(1...8º) orb
            case .trine: return "△" // 120º ~(1...8º) orb
            case .biquintile: return "⦦" // 144º ~(1...2º) orb
            case .quincunx: return "⌅" // 150º ~(1...2º) orb  aka: inconjunct
            case .opposition: return "☍" // 180º ~(1...8º) orb
            }
        }
        
        var defaultDescription:String {
            switch self {
            case .conjunction: return "Relationships, the blurring of differences"
            case .semisextile: return "Dissociation, helping another"
            case .novile: return "Initiation, successful"
            case .semisquare: return "Friction, prompt action to reduce friction"
            case .sextile: return "Friendly, with some talent, ease, and oomph"
            case .quintile: return "Unleashed talent, use of creative energy"
            case .square: return "Tension, expect difficulty and growth"
            case .trine: return "Support, pleasure"
            case .biquintile: return "Unleashed talent, use of creative energy"
            case .quincunx: return "Challenging, misunderstanding and difference"
            case .opposition: return "Relationships, divided loyalties"
            }
        }
    }
    
    enum AspectBody:String, CaseIterable {
        case moon
        case sun
        case mercury
        case venus
        case mars
        case jupiter
        case saturn
        case uranus
        case neptune
        case pluto
        
        init?(with planet:PlanetaryBase) {
            switch planet.planetaryObject {
            case .MERCURY: self = .mercury
            case .VENUS: self = .venus
            case .MARS: self = .mars
            case .JUPITER: self = .jupiter
            case .SATURN: self = .saturn
            case .URANUS: self = .uranus
            case .NEPTUNE: self = .neptune
            default: return nil
            }
        }
        
        init?(with pluto:Pluto) {
            self = .pluto
        }
        
        init?(with sun:Sun) {
            self = .sun
        }
        
        var symbol:String {
            switch self {
                case .moon: return "☽"
                case .sun: return "☉"
                case .mercury: return "☿"
                case .venus: return "♀"
                case .mars: return "♂︎"
                case .jupiter: return "♃"
                case .saturn: return "♄"
                case .uranus: return "♅"
                case .neptune: return "♆"
                case .pluto: return "♇"
            }
        }
        
        var defaultDescription:String {
            switch self {
            case .moon: return "Feelings, moods and senses"
            case .sun: return "Core, self and identity"
            case .mercury: return "Communication, thinking and reason"
            case .venus: return "Favorite, attraction, pleasure"
            case .mars: return "Action, bravery and agression"
            case .jupiter: return "Motivation, abundance and growth"
            case .saturn: return "Authority, boundaries and rules"
            case .uranus: return "Surpise, reversals and breakthroughs"
            case .neptune: return "Romance, avoidance and fantasy"
            case .pluto: return "Destruction, reincarnation and regeneration"
            }
        }
    }
    
    struct Aspect {
        var primarybody:AspectBody
        var relation:AspectRelation
        var secondaryBody:AspectBody
        
        var combinedDescription:String {
            let description = self.description
            let planetaryEffectDescription = self.planetaryEffectDescription()
            if description.count == planetaryEffectDescription.count {
                return self.planetaryEffectDescription(flipPlanets: true)
            }
            return planetaryEffectDescription
        }
        
        func angleDiff(for date:Date, magnitude:Bool = true) -> Degree {
            
            guard let p1 = self.primarybody.celestialLongitude(date),
                let p2 = self.secondaryBody.celestialLongitude(date) else { return 0 }
            
            let d = p1 - p2
            
            return magnitude ? abs(d) : d
        }
        
        var description:String {
            return primarybody.defaultDescription + relation.defaultDescription + secondaryBody.defaultDescription
        }
        
        //
        func planetaryEffectDescription(flipPlanets:Bool = false) -> String {
            
            let primarybody = flipPlanets ? self.secondaryBody : self.primarybody
            let secondaryBody = flipPlanets ? self.primarybody : self.secondaryBody
            
            switch primarybody {
            case .sun:
                switch secondaryBody {
                case .moon:
                    switch relation {
                    case .conjunction: return self.description + "Revitalizing, new beginnings"
                    case .sextile: return self.description + "Gain through more work"
                    case .square: return self.description + "Don't force matter; patience needed"
                    case .trine: return self.description + "Ease with the opposite sex"
                    case .quincunx: return self.description + "Period of self-examination and transformation"
                    case .opposition: return self.description + "Hard work for little gain"
                    default: return self.description
                    }
                case .mercury:
                    switch relation {
                    case .conjunction: return self.description + "Short trip; pay attention to details"
                    default: return self.description
                    }
                case .venus:
                    switch relation {
                    case .conjunction: return self.description + "Personal charm energized"
                    default: return self.description
                    }
                case .mars:
                    switch relation {
                    case .conjunction: return self.description + "Job accented; high energy, quarrels"
                    case .sextile: return self.description + "Nervous energy; need self-control"
                    case .square: return self.description + "Use restraint; quick acting"
                    case .trine: return self.description + "Finish projects, meet people"
                    case .quincunx: return self.description + "Fitful bursts of dynamic action"
                    case .opposition: return self.description + "Quarrels, energy needs direction"
                    default: return self.description
                    }
                case .jupiter:
                    switch relation {
                    case .conjunction: return self.description + "Get out of a rut; philosophical"
                    case .sextile: return self.description + "Optimistic; big promises and dreams"
                    case .square: return self.description + "Personal problems; be philosophical"
                    case .trine: return self.description + "Financial opportunities, self-assurance"
                    case .quincunx: return self.description + "Exaggerated self-image can cause disagreements"
                    case .opposition: return self.description + "Extravagance, exaggeration, wasted time"
                    default: return self.description
                    }
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Think seriously about life direction"
                    case .sextile: return self.description + "Success; patient, steady efforts"
                    case .square: return self.description + "Losses from gambling; low energy"
                    case .trine: return self.description + "Good for dealing with authority"
                    case .quincunx: return self.description + "Minor obsticles presented by authority figures"
                    case .opposition: return self.description + "Hard work; responsibilites pile up"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "Keep mind on job, magnetism"
                    case .sextile: return self.description + "Original, put creative ideas into action"
                    case .square: return self.description + "Make mistakes, keep action steady"
                    case .trine: return self.description + "Excitement and fun, life of the party"
                    case .quincunx: return self.description + "Rebellion against selfish interest"
                    case .opposition: return self.description + "Resentment, dicord; be tactful"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Active imagination, inspiration"
                    case .sextile: return self.description + "Meditation, inner understanding"
                    case .square: return self.description + "Judgement poor; postpone decisions"
                    case .trine: return self.description + "Idealism, friendship, romance"
                    case .quincunx: return self.description + "Opportunity to glimpse own spiritual nature"
                    case .opposition: return self.description + "Impractical, idealistic"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Increased aggressiveness, independence"
                    case .sextile: return self.description + "Community groups, creative changes"
                    case .square: return self.description + "Others' plans conflict with yours"
                    case .trine: return self.description + "Make progressive changes"
                    case .quincunx: return self.description + "Struggle between ego and spiritual will"
                    case .opposition: return self.description + "More agressive; possible unwise action"
                    default: return self.description
                    }
                default: return self.description
                }
            case .moon:
                switch secondaryBody {
                case .mercury:
                    switch relation {
                    case .conjunction: return self.description + "Temperamental actions and words"
                    case .sextile: return self.description + "Quick thinking, many ideas"
                    case .square: return self.description + "Restlessness, indecision, worry"
                    case .trine: return self.description + "Reach decisions, persuade others"
                    case .quincunx: return self.description + "Need for balancing thinking and emotions"
                    case .opposition: return self.description + "Handle routine work and details"
                    default: return self.description
                    }
                case .venus:
                    switch relation {
                    case .conjunction: return self.description + "Ideas of beauty and decoration"
                    case .sextile: return self.description + "Harmony; affectionate, cheerful"
                    case .square: return self.description + "Relax with friends, extravagance"
                    case .trine: return self.description + "Beautiful purchases, redecoration"
                    case .quincunx: return self.description + "Discrimination required in romantic situations"
                    case .opposition: return self.description + "Excess in emotions, extravagance"
                    default: return self.description
                    }
                case .mars:
                    switch relation {
                    case .conjunction: return self.description + "Keep active, finish tasks"
                    case .sextile: return self.description + "Nervousness and excitement"
                    case .square: return self.description + "Impulsive, emotional thinking"
                    case .trine: return self.description + "Harmony; cheerful and exciting"
                    case .quincunx: return self.description + "Direct, impulsive emotions"
                    case .opposition: return self.description + "High energy, but not cooperation"
                    default: return self.description
                    }
                case .jupiter:
                    switch relation {
                    case .conjunction: return self.description + "Contentment, optimism; idealistic"
                    case .sextile: return self.description + "Cheerful; cooperation"
                    case .square: return self.description + "Excess, broken promises; impractical"
                    case .trine: return self.description + "Overly optimistic progress with ideas"
                    case .quincunx: return self.description + "Questions concerning philosophical outlook"
                    case .opposition: return self.description + "Extravagance, should seek enjoyment"
                    default: return self.description
                    }
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Dependability, responsibility"
                    case .sextile: return self.description + "Easy to help those in need; good advice"
                    case .square: return self.description + "Disciplined work, serious thinking"
                    case .trine: return self.description + "Accomplishment through patience"
                    case .quincunx: return self.description + "Need to examine repressed emotions"
                    case .opposition: return self.description + "Stick with plans, efficency; budget time"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "High hopes, unrealistic plans"
                    case .sextile: return self.description + "Original, inventive, creative"
                    case .square: return self.description + "Erratic or eccentric behavior, quick mind"
                    case .trine: return self.description + "Originality; influence others"
                    case .quincunx: return self.description + "Abrupt changes in moods unsettle old patterns"
                    case .opposition: return self.description + "Distractions, unvonventional acts or thoughts"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Distractions, sensitive emotions"
                    case .sextile: return self.description + "Intuitions, creativity, meditations"
                    case .square: return self.description + "Judgement poor; gullible, impressionable"
                    case .trine: return self.description + "Idealistic, romantic, friendly"
                    case .quincunx: return self.description + "Discriminate between apathy and relaxation"
                    case .opposition: return self.description + "Distruct intuition, postpone decisions"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Involvement with others, quiet conversations"
                    case .sextile: return self.description + "Enlightening descussions, intense feelings"
                    case .square: return self.description + "Make few demands on others and yourself"
                    case .trine: return self.description + "Romance, pleasure, popularity"
                    case .quincunx: return self.description + "Emotional upheavals threan inner security"
                    case .opposition: return self.description + "Daydreams, snags in plans"
                    default: return self.description
                    }
                default: return self.description
                }
            case .mercury:
                switch secondaryBody {
                case .venus:
                    switch relation {
                    case .conjunction: return self.description + "More artistic and pleasant"
                    case .sextile: return self.description + "Emotional happiness and calm"
                    case .square: return self.description + "Write letters, make phone calls"
                    case .trine: return self.description + "Unexpected meetings, social invitations"
                    case .quincunx: return self.description + "Misunderstood affection"
                    case .opposition: return self.description + "Meet new people, conversations"
                    default: return self.description
                    }
                case .mars:
                    switch relation {
                    case .conjunction: return self.description + "Ideas abound; impulsive, easy communications"
                    case .sextile: return self.description + "Good sense of humor, social ease"
                    case .square: return self.description + "Touchy; challenge in communications"
                    case .trine: return self.description + "Quick mind; can get your point across"
                    case .quincunx: return self.description + "Avoid nervous overstrain"
                    case .opposition: return self.description + "Be tactful, could have arguments"
                    default: return self.description
                    }
                case .jupiter:
                    switch relation {
                    case .conjunction: return self.description + "Good news; study; tolerant"
                    case .sextile: return self.description + "Reunions, travel plans, new ideas"
                    case .square: return self.description + "Quick to jump to conclusions"
                    case .trine: return self.description + "Interesting and reqarding work"
                    case .quincunx: return self.description + "exaggerated ideas cloud judgement"
                    case .opposition: return self.description + "Be practical; the center of everyone's attention"
                    default: return self.description
                    }
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Serious thinking; attention to details"
                    case .sextile: return self.description + "Plan ahead; good judgement"
                    case .square: return self.description + "Be diplomatic, avoid stubbornness"
                    case .trine: return self.description + "Make realistic decisions for your future"
                    case .quincunx: return self.description + "Laborious thinking impedes communication"
                    case .opposition: return self.description + "Delay in plans, watch what you put into writing"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "Mind sparks with original ideas"
                    case .sextile: return self.description + "Can find support for your ideas"
                    case .square: return self.description + "Sarcastic; don't worry about things"
                    case .trine: return self.description + "New friends; social life exciting"
                    case .quincunx: return self.description + "Need to concentrate on one interest at a time"
                    case .opposition: return self.description + "Temperamental; many small irritations"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Confused or idealistic thinking"
                    case .sextile: return self.description + "Intuitie awareness, cleverness"
                    case .square: return self.description + "Escapist tendencies, laziness"
                    case .trine: return self.description + "Romantic, idealistic thoughts"
                    case .quincunx: return self.description + "Healing through creative visualizations"
                    case .opposition: return self.description + "Gossip, scandalous news"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Be subtle, not forceful"
                    case .sextile: return self.description + "Get small tasks done quickly"
                    case .square: return self.description + "Minor mistakes, overspending"
                    case .trine: return self.description + "Can gain support for special plan"
                    case .quincunx: return self.description + "Implusive, outspoken; some quarrels"
                    case .opposition: return self.description + "Careful analysis of psychological imbalances"
                    default: return self.description
                    }
                default: return self.description
                }
            case .venus:
                switch secondaryBody {
                case .mars:
                    switch relation {
                    case .conjunction: return self.description + "Popular; extravagance, love"
                    case .sextile: return self.description + "Can easily express your feelings"
                    case .square: return self.description + "Extravagance with pleasures and luxuries"
                    case .trine: return self.description + "Can put values and beliefs into action"
                    case .quincunx: return self.description + "Sexual desires need refined expression"
                    case .opposition: return self.description + "Can be imposed on; sensitive feelings"
                    default: return self.description
                    }
                case .jupiter:
                    switch relation {
                    case .conjunction: return self.description + "Life seems happier, more joyful"
                    case .sextile: return self.description + "Friendly to all; lighthearted"
                    case .square: return self.description + "Personal ubset; sensitive feelings"
                    case .trine: return self.description + "You recieve the rewards you deserve"
                    case .quincunx: return self.description + "Reassessment of a romantic partner"
                    case .opposition: return self.description + "Be practical and realistic in all plans"
                    default: return self.description
                    }
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Make plans for parties and get-togethers"
                    case .sextile: return self.description + "New career opportunities, success"
                    case .square: return self.description + "May be sarcastic with loved ones"
                    case .trine: return self.description + "Sincere, realistic, stable"
                    case .quincunx: return self.description + "Unconscious scruples upset romantic harmony"
                    case .opposition: return self.description + "Don't compare yourself with others; duty"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "May be attracted to a new love interest"
                    case .sextile: return self.description + "Peaceful thoughts end arguments"
                    case .square: return self.description + "Excitement in love life"
                    case .trine: return self.description + "Surround yourself with beauty and pleasure"
                    case .quincunx: return self.description + "Restlessness in a relationship; seeking freedom"
                    case .opposition: return self.description + "Impulsive feelings, changes in mood"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Creative, romantic time"
                    case .sextile: return self.description + "Can recieve a cherished hope or wish"
                    case .square: return self.description + "Let your light and your talents shine"
                    case .trine: return self.description + "Redecoration, creativity, daydreaming"
                    case .quincunx: return self.description + "Express musical inspirations"
                    case .opposition: return self.description + "Impractical idealism, deceptive thoughts"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Don't force a commitment from a loved one"
                    case .sextile: return self.description + "Take the initiative, don't sit at home"
                    case .square: return self.description + "May judge others too harshly"
                    case .trine: return self.description + "Romantic happiness, friendships"
                    case .quincunx: return self.description + "A fading relationship dies"
                    case .opposition: return self.description + "Exciting romance could start"
                    default: return self.description
                    }
                default: return self.description
                }
            case .mars:
                switch secondaryBody {
                case .jupiter:
                    switch relation {
                    case .conjunction: return self.description + "Optimistic, willing to take a chance"
                    case .sextile: return self.description + "Can use your talents to get what you want"
                    case .square: return self.description + "Urge to get away from everything"
                    case .trine: return self.description + "Can make progress at work and home"
                    case .quincunx: return self.description + "Overly exuberant"
                    case .opposition: return self.description + "Avoid extravagance, add to your security"
                    default: return self.description
                    }
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Tackle all projects that take a lot of energy"
                    case .sextile: return self.description + "Work goes smoothly if preplanned"
                    case .square: return self.description + "Duties may be forced on you by others"
                    case .trine: return self.description + "Good time for reunion with old friends or family"
                    case .quincunx: return self.description + "Nervous restraint"
                    case .opposition: return self.description + "Nervousness, inability to act"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "Take it easy, don't get excited"
                    case .sextile: return self.description + "Good with anything you attempt; success"
                    case .square: return self.description + "False starts, accidents, high-strung"
                    case .trine: return self.description + "Think about your future, not your past"
                    case .quincunx: return self.description + "Rash and impulsive actions"
                    case .opposition: return self.description + "Self-control in thinking and acting needed"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Impracticality with money and energy"
                    case .sextile: return self.description + "Changes can lead to excitement"
                    case .square: return self.description + "Laziness, procrastination, religious fanaticism"
                    case .trine: return self.description + "Intuitively know what to do and how to do it"
                    case .quincunx: return self.description + "Under-energized, delusional dreams"
                    case .opposition: return self.description + "Don't force others to act when you don't"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Difficult to handle personal matters"
                    case .sextile: return self.description + "Will be able to tackle any problem"
                    case .square: return self.description + "Not the time to make changes in your life"
                    case .trine: return self.description + "Can clear away the clutter in your life"
                    case .quincunx: return self.description + "Restlessness and unease; causes unknown"
                    case .opposition: return self.description + "Restlessness; strong desire for changes"
                    default: return self.description
                    }
                default: return self.description
                }
            case .jupiter:
                switch secondaryBody {
                case .saturn:
                    switch relation {
                    case .conjunction: return self.description + "Orderly; prudent expansion toward objectives"
                    case .sextile: return self.description + "Confidence and achievement"
                    case .square: return self.description + "Lack of purpose and faith; Ill-timing"
                    case .trine: return self.description + "Faith in destiny; inspired constructiveness"
                    case .quincunx: return self.description + "Restlessness and unease"
                    case .opposition: return self.description + "Vacillation and doubt of goals and ambitions"
                    default: return self.description
                    }
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "Unexpected good fortune or understanding"
                    case .sextile: return self.description + "New consideration"
                    case .square: return self.description + "Zesty pursuit or unfeasible tangents"
                    case .trine: return self.description + "New and firtuitous insights"
                    case .quincunx: return self.description + "Distruct of shared values and ideals"
                    case .opposition: return self.description + "Disorienting, sudden developments"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Creative and spiritual optimism"
                    case .sextile: return self.description + "Mystical inspiration"
                    case .square: return self.description + "Unsound approach to abstract, mystical ideas"
                    case .trine: return self.description + "Access to universal love and creativity"
                    case .quincunx: return self.description + "Beliefs overstep ideals"
                    case .opposition: return self.description + "Hold conflicting views about reality and idealism"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Efforts at psychological improvement"
                    case .sextile: return self.description + "Interest in spiritual, psychological, occult ideas"
                    case .square: return self.description + "Coercive use of willpower for a \"spiritual\" goal"
                    case .trine: return self.description + "Spiritual, psychological regeneration and growth"
                    case .quincunx: return self.description + "Conflict between truth and emotions"
                    case .opposition: return self.description + "Gradiose, exploitive schemes that tend to fail"
                    default: return self.description
                    }
                default: return self.description
                }
            case .saturn:
                switch secondaryBody {
                case .uranus:
                    switch relation {
                    case .conjunction: return self.description + "Tension to build; constructive alertness"
                    case .sextile: return self.description + "Limited creative freedom"
                    case .square: return self.description + "Conflict between independence and success"
                    case .trine: return self.description + "Success where others fail; quick insight"
                    case .quincunx: return self.description + "Uptight about limited independence"
                    case .opposition: return self.description + "Frustrating resistance, non-submission, accidents"
                    default: return self.description
                    }
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "Focus on spiritual objectives; mystical cynicism"
                    case .sextile: return self.description + "Spiritual insights further ambitions"
                    case .square: return self.description + "Escape from responsibility; loss of ambition"
                    case .trine: return self.description + "Hidden resources give support"
                    case .quincunx: return self.description + "Imagination is distrusted"
                    case .opposition: return self.description + "Hidden influences impede material goals"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Externalization of psychological realities"
                    case .sextile: return self.description + "Increased self-discipline and moral integrity"
                    case .square: return self.description + "Watch out for dangerous circumstances"
                    case .trine: return self.description + "Willpower to accomplish objectives easily"
                    case .quincunx: return self.description + "Haunting fear of failure"
                    case .opposition: return self.description + "Coercive suppression by self or others"
                    default: return self.description
                    }
                default: return self.description
                }
            case .uranus:
                switch secondaryBody {
                case .neptune:
                    switch relation {
                    case .conjunction: return self.description + "New mystical, spiritual impressions and feelings"
                    case .sextile: return self.description + "New interests in the spiritual side of life"
                    case .square: return self.description + "Deluded freedom, sudden mistaken impressions"
                    case .trine: return self.description + "Sudden helpful precognitions, imaginations"
                    case .quincunx: return self.description + "Hidden, revolutionary disturbances"
                    case .opposition: return self.description + "Erratic behavior caused by deluded motivations"
                    default: return self.description
                    }
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Sudden expression of strong emotions"
                    case .sextile: return self.description + "New psychological awareness"
                    case .square: return self.description + "Emotional strife, fanaticism, upsets, disturbance"
                    case .trine: return self.description + "Powerful, helpful release of emotional energy"
                    case .quincunx: return self.description + "Uncorrdinated energy inputs and outputs"
                    case .opposition: return self.description + "Ideals oppose emotional drive"
                    default: return self.description
                    }
                default: return self.description
                }
            case .neptune:
                switch secondaryBody {
                case .pluto:
                    switch relation {
                    case .conjunction: return self.description + "Imagination and desire unite"
                    case .sextile: return self.description + "Desire to create"
                    case .square: return self.description + "Desire impeded by delusion"
                    case .trine: return self.description + "Spiritual goodwill; help from beyond"
                    case .quincunx: return self.description + "Deluded drive; emotion oversteps reality"
                    case .opposition: return self.description + "Unconcious conflict"
                    default: return self.description
                    }
                default: return self.description
                }
            default: return self.description
            }
        }
    }
    
}
